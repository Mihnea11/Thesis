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
        private readonly NotificationService notificationService;

        private readonly string baseUrl = "http://127.0.0.1:8000";
        private static ConcurrentDictionary<string, ConfigurationSessionModel> sessions = new ConcurrentDictionary<string, ConfigurationSessionModel>();

        public ModelOPSController(HttpClient httpClient, NotificationService notificationService)
        {
            this.httpClient = httpClient;
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
    }
}
