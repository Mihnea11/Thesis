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

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class FileController : ControllerBase
    {
        private readonly UserService userService;
        private readonly NotificationService notificationService;

        private static ConcurrentDictionary<string, UploadSessionModel> uploadSessions = new ConcurrentDictionary<string, UploadSessionModel>();

        public FileController(UserService userService, NotificationService notificationService)
        {
            this.userService = userService;
            this.notificationService = notificationService;
        }

        [HttpGet("Labels")]
        public async Task<IActionResult> GetLabels()
        {
            var authorizationHeader = HttpContext.Request.Headers["Authorization"].ToString();
            if (string.IsNullOrEmpty(authorizationHeader) || !authorizationHeader.StartsWith("Bearer "))
            {
                return Unauthorized("No JWT token provided.");
            }

            var token = authorizationHeader.Substring("Bearer ".Length).Trim();
            if (string.IsNullOrEmpty(token))
            {
                return Unauthorized("JWT token is empty.");
            }

            string userId;
            try
            {
                userId = await GetUserIdFromToken(token);
            }
            catch (Exception ex)
            {
                return Unauthorized($"Token error: {ex.Message}");
            }

            var rootPath = FileStorageHelper.GetDataStoragePath();
            var userPath = Path.Combine(rootPath, userId);

            if (!Directory.Exists(userPath))
            {
                return NotFound("User directory not found.");
            }

            var labels = Directory.GetDirectories(userPath).Select(Path.GetFileName).ToList();

            return Ok(labels);
        }

        [HttpPost("StartUpload")]
        public async Task<IActionResult> StartUploadSession([FromBody] UploadSessionInitModel initModel)
        {
            var authorizationHeader = HttpContext.Request.Headers["Authorization"].ToString();
            if (string.IsNullOrEmpty(authorizationHeader) || !authorizationHeader.StartsWith("Bearer "))
            {
                return Unauthorized("No JWT token provided.");
            }

            var token = authorizationHeader.Substring("Bearer ".Length).Trim();
            if (string.IsNullOrEmpty(token))
            {
                return Unauthorized("JWT token is empty.");
            }

            string userId;
            try
            {
                userId = await GetUserIdFromToken(token);
            }
            catch (Exception ex)
            {
                return Unauthorized($"Token error: {ex.Message}");
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

        [HttpPost("UploadChunk/{sessionId}")]
        public async Task<IActionResult> UploadChunk(string sessionId, [FromForm] FileChunkModel chunkModel)
        {
            if(!uploadSessions.TryGetValue(sessionId, out var uploadSession))
            {
                return NotFound("Session ID not found.");
            }

            var authorizationHeader = HttpContext.Request.Headers["Authorization"].ToString();
            if (string.IsNullOrEmpty(authorizationHeader) || !authorizationHeader.StartsWith("Bearer "))
            {
                return Unauthorized("No JWT token provided.");
            }

            var token = authorizationHeader.Substring("Bearer ".Length).Trim();
            if (string.IsNullOrEmpty(token))
            {
                return Unauthorized("JWT token is empty.");
            }

            string userId;
            try
            {
                userId = await GetUserIdFromToken(token);
            }
            catch (Exception ex)
            {
                return Unauthorized($"Token error: {ex.Message}");
            }

            var rootPath = FileStorageHelper.GetDataStoragePath();
            var userPath = Path.Combine(rootPath, userId);
            var labelPath = Path.Combine(userPath, chunkModel.Label);

            var targetDirPath = chunkModel.FileName.Equals("explanatory_file.csv", StringComparison.OrdinalIgnoreCase) ? Path.Combine(labelPath, "explanatory") : labelPath;
            if (!Directory.Exists(targetDirPath))
            {
                Directory.CreateDirectory(targetDirPath);
            }

            var targetFilePath = Path.Combine(targetDirPath, chunkModel.FileName.Equals("explanatory_file.csv", StringComparison.OrdinalIgnoreCase) ? "explanatory_data.csv" : chunkModel.FileName);
            var chunkFilePath = Path.Combine(targetDirPath, $"{chunkModel.FileName}.part{chunkModel.ChunkIndex}");

            try
            {
                using (var stream = new FileStream(chunkFilePath, FileMode.Create))
                {
                    await chunkModel.ChunkFile.CopyToAsync(stream);
                }

                if (chunkModel.ChunkIndex == chunkModel.TotalChunks - 1)
                {
                    await ReassembleFile(targetFilePath, targetDirPath, chunkModel.FileName, chunkModel.TotalChunks);
                    uploadSession.FilesUploaded++;

                    if (uploadSession.FilesUploaded == uploadSession.TotalFiles)
                    {
                        NotificationModel notification = new()
                        {
                            Id = Guid.NewGuid(),
                            UserId = userId,
                            Message = "All files have been uploaded successfully."
                        };

                        await notificationService.AddNotificationAsync(notification);
                        if (uploadSessions.TryRemove(sessionId, out var removedSession))
                        {
                            Console.WriteLine($"Session {sessionId} completed and removed successfully.");
                        }
                        else
                        {
                            Console.WriteLine($"Failed to remove session {sessionId}.");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                await SendErrorNotification(userId, sessionId, uploadSession.FilesUploaded, uploadSession.TotalFiles);

                Console.WriteLine($"Error uploading chunk {chunkModel.ChunkIndex} of {chunkModel.FileName}: {ex.Message}");
                return StatusCode(500, "An error occurred during the file upload.");
            }

            return Ok(new { message = $"Chunk {chunkModel.ChunkIndex} of {chunkModel.FileName} uploaded successfully" });
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

        private async Task<string> GetUserIdFromToken(string token)
        {
            var handler = new JwtSecurityTokenHandler();
            var jwtSecurityToken = handler.ReadJwtToken(token);

            var emailClaim = jwtSecurityToken.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Email)?.Value;
            if (emailClaim == null)
            {
                throw new ArgumentException("Token does not contain an email claim");
            }

            var user = await userService.GetUserByEmailAsync(emailClaim);
            if (user == null)
            {
                throw new InvalidOperationException("User not found");
            }

            return user.Id.ToString();
        }

        private async Task SendErrorNotification(string userId, string sessionId, int filesUploaded, int totalFiles)
        {
            if (uploadSessions.TryRemove(sessionId, out var removedSession))
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
    }
}
