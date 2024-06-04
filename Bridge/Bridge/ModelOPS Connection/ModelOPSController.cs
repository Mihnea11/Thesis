using Bridge.ModelOPS_Connection.Models;
using Bridge.Models;
using Bridge.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Concurrent;
using System.Security.Claims;
using System.Text;
using System.Text.Json;

namespace Bridge.ModelOPS_Connection
{
    [Route("[controller]")]
    [ApiController]
    public class ModelOPSController : ControllerBase
    {
        private readonly HttpClient httpClient;
        private readonly MinioService minioService;
        private readonly NotificationService notificationService;

        private readonly string baseUrl = "http://127.0.0.1:8000";
        private static ConcurrentDictionary<string, ConfigurationSessionModel> sessions = new ConcurrentDictionary<string, ConfigurationSessionModel>();

        public ModelOPSController(HttpClient httpClient, MinioService minioService, NotificationService notificationService)
        {
            this.httpClient = httpClient;
            this.minioService = minioService;
            this.notificationService = notificationService;
        }

        [HttpPost("StartSession")]
        public IActionResult StartSession()
        {
            var userId = GetUserIdFromToken();
            var sessionId = Guid.NewGuid().ToString();

            var session = new ConfigurationSessionModel
            {
                UserId = userId,
                SessionId = sessionId,
                State = "Initialized"
            };

            sessions.TryAdd(sessionId, session);
            return Ok(new { SessionId = sessionId });
        }

        [HttpPost("DownloadFiles/{sessionId}")]
        public async Task<IActionResult> DownloadFiles([FromBody] FileDownloadRequestModel request, string sessionId)
        {
            if (!sessions.TryGetValue(sessionId, out var session))
            {
                return NotFound("Session not found.");
            }

            if (session.UserId != GetUserIdFromToken())
            {
                return Unauthorized("Unauthorized access.");
            }

            string url = baseUrl + "/download_files";
            try
            {
                request.BucketName = "thesis-data";
                request.UserId = session.UserId;

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    FileDownloadResponseModel? result = JsonSerializer.Deserialize<FileDownloadResponseModel>(responseContent);

                    if (result == null)
                    {
                        session.State = "DownloadFailed";
                        await SendErrorNotification(session.UserId, sessionId);
                        return BadRequest("Failed to download files: " + response.StatusCode);
                    }

                    session.TemporaryDirectory = result.FilePath;
                    session.State = "Downloaded";
                    return Ok(responseContent);
                }
                else
                {
                    session.State = "DownloadFailed";
                    await SendErrorNotification(session.UserId, sessionId);
                    return BadRequest("Failed to download files: " + response.StatusCode);
                }
            }
            catch (Exception ex)
            {
                session.State = "Error";
                await SendErrorNotification(session.UserId, sessionId);
                return StatusCode(500, "Internal server error: " + ex.Message);
            }
        }

        [HttpPost("CleanFiles/{sessionId}")]
        public async Task<IActionResult> CleanFiles([FromBody] FileCleaningRequestModel request, string sessionId)
        {
            if (!sessions.TryGetValue(sessionId, out var session))
            {
                return NotFound("Session not found.");
            }

            if (session.UserId != GetUserIdFromToken())
            {
                return Unauthorized("Unauthorized access.");
            }

            string url = baseUrl + "/clean_files";
            var cleaningRequest = new FileCleaningRequestModel
            {
                InputPath = session.TemporaryDirectory,
                PatientIdentifier = string.IsNullOrEmpty(request.PatientIdentifier) ? "defaultIdentifier" : request.PatientIdentifier,
                EncodingMethod = string.IsNullOrEmpty(request.EncodingMethod) ? "label" : request.EncodingMethod,
                ScaleMethod = string.IsNullOrEmpty(request.ScaleMethod) ? "standardize" : request.ScaleMethod,
                ExcludedColumns = request.ExcludedColumns ?? new List<string>()
            };

            try
            {
                var json = JsonSerializer.Serialize(cleaningRequest);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    FileCleaningResponseModel? result = JsonSerializer.Deserialize<FileCleaningResponseModel>(responseContent);

                    if (result == null)
                    {
                        session.State = "DownloadFailed";
                        await SendErrorNotification(session.UserId, sessionId);
                        return BadRequest("Failed to download files: " + response.StatusCode);
                    }

                    session.TemporaryDirectory = result.FilePath;
                    session.State = "Downloaded";
                    return Ok(responseContent);
                }
                else
                {
                    session.State = "CleanFailed";
                    await SendErrorNotification(session.UserId, sessionId);
                    return BadRequest("Failed to clean files: " + response.StatusCode);
                }
            }
            catch (Exception ex)
            {
                session.State = "Error";
                await SendErrorNotification(session.UserId, sessionId);
                return StatusCode(500, "Internal server error: " + ex.Message);
            }
        }

        [HttpPost("TrainModel/{sessionId}")]
        public async Task<IActionResult> TrainModel([FromBody] TrainModelRequestModel request, string sessionId)
        {
            if (!sessions.TryGetValue(sessionId, out var session))
            {
                return NotFound("Session not found.");
            }

            if (session.UserId != GetUserIdFromToken())
            {
                return Unauthorized("Unauthorized access.");
            }

            session.State = "TrainingStarted";

            string url = baseUrl + "/train_model";
            try
            {
                request.BucketName = "thesis-results";
                request.InputPath = session.TemporaryDirectory;
                request.UserId = session.UserId;

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();

                    session.State = "TrainingCompleted";
                    await SendSuccessNotification(session.UserId, responseContent);

                    return Ok(responseContent);
                }
                else
                {
                    session.State = "TrainingFailed";
                    await SendErrorNotification(session.UserId, sessionId);
                    return BadRequest("Failed to train model: " + response.StatusCode);
                }
            }
            catch (Exception ex)
            {
                session.State = "Error";
                await SendErrorNotification(session.UserId, sessionId);
                return StatusCode(500, "Internal server error: " + ex.Message);
            }
        }

        [HttpGet("Results/Features/{label}")]
        public async Task<IActionResult> GetExtractedFeatures(string label)
        {
            string userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("User ID not found in token.");
            }

            string bucketName = "thesis-results";
            string fileName = "feature_importances.txt";

            try
            {
                var featureImportances = await minioService.GetFileContentAsJsonAsync(bucketName, userId, label, fileName);

                if (featureImportances != null && featureImportances.Count > 0)
                {
                    return Ok(featureImportances);
                }
                else
                {
                    return NotFound("No feature importances data found.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error retrieving feature importances: {ex.Message}");
                return StatusCode(500, "Internal server error while retrieving features.");
            }
        }

        [HttpGet("Results/Graphics/{label}/{start}:{count}")]
        public async Task<IActionResult> GetGeneratedGraphics(string label, int start, int count)
        {
            string userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("User ID not found in token.");
            }

            string bucketName = "thesis-results";
            string prefix = $"{userId}/{label}/graphics/";

            try
            {
                var images = await minioService.GetImagesAsync(bucketName, prefix, start, count);

                if (images != null && images.Count > 0)
                {
                    return Ok(images);
                }
                else
                {
                    return NotFound("No images found.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error retrieving images: {ex.Message}");
                return StatusCode(500, "Internal server error while retrieving images.");
            }
        }

        [HttpGet("Results/Stats/{label}/{start}:{count}")]
        public async Task<IActionResult> GetStats(string label, int start, int count)
        {
            string userId = GetUserIdFromToken();
            if (string.IsNullOrEmpty(userId))
            {
                return Unauthorized("User ID not found in token.");
            }

            string bucketName = "thesis-results";
            string prefix = $"{userId}/{label}/stats/";

            try
            {
                var images = await minioService.GetImagesAsync(bucketName, prefix, start, count);

                if (images != null && images.Count > 0)
                {
                    return Ok(images);
                }
                else
                {
                    return NotFound("No images found.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error retrieving images: {ex.Message}");
                return StatusCode(500, "Internal server error while retrieving images.");
            }
        }

        private string GetUserIdFromToken()
        {
            var principal = HttpContext.User;
            var userId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;

            return userId;
        }

        private async Task SendErrorNotification(string userId, string sessionId)
        {
            if (sessions.TryRemove(sessionId, out _))
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
                Message = $"An error occurred during the model configuration process. Please try again later."
            };

            await notificationService.AddNotificationAsync(notification);
        }

        private async Task SendSuccessNotification(string userId, string sessionId)
        {

            NotificationModel notification = new()
            {
                Id = Guid.NewGuid(),
                UserId = userId,
                Message = $"Your model has finished training. You can now check the results."
            };

            await notificationService.AddNotificationAsync(notification);

            if (sessions.TryRemove(sessionId, out _))
            {
                Console.WriteLine($"Session {sessionId} finished and removed successfully.");
            }
            else
            {
                Console.WriteLine($"Failed to remove session {sessionId}.");
            }
        }
    }
}
