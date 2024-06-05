using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Bridge.Models;
using Bridge.Utility;
using Bridge.Services;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using Microsoft.AspNetCore.SignalR;
using Bridge.Hubs;
using System.Collections.Concurrent;
using Microsoft.IdentityModel.Tokens;

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class FileController : ControllerBase
    {
        private readonly MinioService minioService;
        private readonly NotificationService notificationService;

        private static ConcurrentDictionary<string, UploadSessionModel> uploadSessions = new ConcurrentDictionary<string, UploadSessionModel>();

        public FileController(MinioService minioService, NotificationService notificationService)
        {
            this.minioService = minioService;
            this.notificationService = notificationService;
        }

        [HttpGet("Labels")]
        public async Task<IActionResult> GetLabels()
        {
            var userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("JWT token is invalid or missing.");
            }

            try
            {
                var labels = await minioService.ListUserLabelsAsync("thesis-data", userId);
                return Ok(labels);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error retrieving labels: {ex.Message}");
            }
        }

        [HttpGet("Files")]
        public async Task<IActionResult> ListFiles([FromQuery] string label)
        {
            var userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("JWT token is invalid or missing.");
            }

            try
            {
                var files = await minioService.ListFilesByLabelAsync("thesis-data", userId, label);
                return Ok(files);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error retrieving files: {ex.Message}");
            }
        }

        [HttpDelete("File")]
        public async Task<IActionResult> DeleteFileByName([FromQuery] string label, [FromQuery] string fileName)
        {
            var userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("JWT token is invalid or missing.");
            }

            try
            {
                var result = await minioService.RemoveFileByNameAsync("thesis-data", userId, label, fileName);
                if (result)
                {
                    return Ok(new { message = "File deleted successfully." });
                }
                else
                {
                    return StatusCode(500, "Error deleting file.");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error deleting file: {ex.Message}");
            }
        }

        [HttpDelete("Label")]
        public async Task<IActionResult> DeleteLabelDirectory([FromQuery] string label)
        {
            var userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("JWT token is invalid or missing.");
            }

            try
            {
                var result = await minioService.RemoveLabelDirectoryAsync("thesis-data", userId, label);
                if (result)
                {
                    return Ok(new { message = "Label directory deleted successfully." });
                }
                else
                {
                    return StatusCode(500, "Error deleting label directory.");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error deleting label directory: {ex.Message}");
            }
        }

        [HttpPost("StartUpload")]
        public IActionResult StartUploadSession([FromBody] UploadSessionInitModel initModel)
        {
            var userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("JWT token is invalid or missing.");
            }

            var sessionId = Guid.NewGuid().ToString();
            var uploadSession = new UploadSessionModel
            {
                SessionId = sessionId,
                TotalFiles = initModel.TotalFiles,
                FilesUploaded = 0,
                UserId = userId
            };

            uploadSessions.TryAdd(sessionId, uploadSession);
            return Ok(new { SessionId = sessionId });
        }

        [HttpPost("Upload/{sessionId}")]
        public async Task<IActionResult> Upload(string sessionId, [FromForm] FileChunkModel chunkModel)
        {
            if (!uploadSessions.TryGetValue(sessionId, out var uploadSession))
            {
                return NotFound("Session ID not found.");
            }

            var userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("JWT token is invalid or missing.");
            }

            var labelPath = chunkModel.FileName.Equals("explanatory_file.csv", StringComparison.OrdinalIgnoreCase) ? chunkModel.Label + "/explanatory_files" : chunkModel.Label;
            var rootDirectory = Path.Combine(Path.GetTempPath(), "Uploads");
            var tempDirectoryPath = Path.Combine(rootDirectory, userId, sessionId, labelPath);
            Directory.CreateDirectory(tempDirectoryPath);

            var chunkFilePath = Path.Combine(tempDirectoryPath, $"{chunkModel.FileName}.part{chunkModel.ChunkIndex}");
            try
            {
                using (var stream = new FileStream(chunkFilePath, FileMode.Create))
                {
                    await chunkModel.ChunkFile.CopyToAsync(stream);
                }

                if (chunkModel.ChunkIndex == chunkModel.TotalChunks - 1)
                {
                    var finalFilePath = Path.Combine(tempDirectoryPath, chunkModel.FileName);

                    await ReassembleFile(finalFilePath, tempDirectoryPath, chunkModel.FileName, chunkModel.TotalChunks);
                    await minioService.UploadFileAsync("thesis-data", $"{userId}/{labelPath}/{chunkModel.FileName}", finalFilePath);

                    uploadSession.FilesUploaded++;
                    if (uploadSession.FilesUploaded == uploadSession.TotalFiles)
                    {
                        await SendCompletionNotification(userId, sessionId, "All files have been uploaded successfully.");

                        await DeleteDirectoryAsync(rootDirectory);
                    }
                }

                return Ok(new { message = $"Chunk {chunkModel.ChunkIndex} of {chunkModel.FileName} uploaded successfully." });
            }
            catch (Exception ex)
            {
                await SendErrorNotification(userId, sessionId, uploadSession.FilesUploaded, uploadSession.TotalFiles);
                return StatusCode(500, $"An error occurred during the file upload: {ex.Message}");
            }
        }
        private string GetUserIdFromToken()
        {
            var principal = HttpContext.User;
            var userId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;

            return userId;
        }

        private async Task ReassembleFile(string targetFilePath, string directoryPath, string fileName, int totalChunks)
        {
            using (var outputFileStream = new FileStream(targetFilePath, FileMode.Create))
            {
                for (int i = 0; i < totalChunks; i++)
                {
                    var chunkFilePath = Path.Combine(directoryPath, $"{fileName}.part{i}");
                    using (var inputChunkStream = new FileStream(chunkFilePath, FileMode.Open))
                    {
                        await inputChunkStream.CopyToAsync(outputFileStream);
                    }
                    System.IO.File.Delete(chunkFilePath);
                }
            }
        }

        private async Task SendCompletionNotification(string userId, string sessionId, string message)
        {
            NotificationModel notification = new()
            {
                Id = Guid.NewGuid(),
                UserId = userId,
                Message = message
            };

            await notificationService.AddNotificationAsync(notification);

            if (uploadSessions.TryRemove(sessionId, out _))
            {
                Console.WriteLine($"Session {sessionId} completed and removed successfully.");
            }
            else
            {
                Console.WriteLine($"Failed to remove session {sessionId}.");
            }
        }

        private async Task SendErrorNotification(string userId, string sessionId, int filesUploaded, int totalFiles)
        {
            if (uploadSessions.TryRemove(sessionId, out _))
            {
                Console.WriteLine($"Session {sessionId} canceled and removed successfully.");
            }
            else
            {
                Console.WriteLine($"Failed to remove session {sessionId}.");
            }

            NotificationModel notification = new()
            {
                Id = Guid.NewGuid(),
                UserId = userId,
                Message = $"An error occurred: {filesUploaded} out of {totalFiles} files have been uploaded."
            };

            await notificationService.AddNotificationAsync(notification);
        }

        private async Task DeleteDirectoryAsync(string path, int maxRetries = 5, int delayMilliseconds = 200)
        {
            for (int attempt = 0; attempt < maxRetries; attempt++)
            {
                try
                {
                    if (Directory.Exists(path))
                    {
                        Directory.Delete(path, true);
                        Console.WriteLine($"Directory successfully deleted: {path}");
                        return;
                    }
                }
                catch (IOException ex)
                {
                    Console.WriteLine($"Attempt {attempt + 1}: IOException, could not delete directory {path}. Error: {ex.Message}");
                }
                catch (UnauthorizedAccessException ex)
                {
                    Console.WriteLine($"Attempt {attempt + 1}: UnauthorizedAccessException, could not delete directory {path}. Error: {ex.Message}");
                }

                await Task.Delay(delayMilliseconds);
            }

            Console.WriteLine($"Failed to delete directory after {maxRetries} attempts.");
        }
    }
}
