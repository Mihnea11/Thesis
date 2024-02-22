using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Bridge.Models;
using Bridge.Utility;
using Bridge.Services;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class FileController : ControllerBase
    {
        private readonly UserService userService;

        public FileController(UserService userService)
        {
            this.userService = userService;
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

        [HttpPost("Upload")]
        public async Task<IActionResult> UploadFiles([FromForm] FileModel uploadModel)
        {
            if (uploadModel.Files == null || !uploadModel.Files.Any())
            {
                return BadRequest("No files uploaded");
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
            var labelPath = Path.Combine(rootPath, uploadModel.Label);

            if (!Directory.Exists(labelPath))
            {
                Directory.CreateDirectory(labelPath);
            }

            foreach (var file in uploadModel.Files)
            {
                if (file.Length <= 0)
                {
                    continue;
                }

                var filePath = Path.Combine(labelPath, file.Name);
                using (var fileStream = new FileStream(filePath, FileMode.Create))
                {
                    await file.CopyToAsync(fileStream);
                }
            }

            return Ok($"{uploadModel.Files.Count} files uploaded successfully");
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
    }
}
