using Microsoft.AspNetCore.Mvc;
using Bridge.Services;
using Bridge.Models;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using Bridge.Utility;

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class TokenController : ControllerBase
    {
        private readonly UserService userService;
        private readonly TokenService refreshTokenService;
        private readonly IConfiguration configuration;

        public TokenController(UserService userService, TokenService refreshTokenService, IConfiguration configuration)
        {
            this.userService = userService;
            this.refreshTokenService = refreshTokenService;
            this.configuration = configuration;
        }

        [HttpPost("ValidateToken")]
        public IActionResult ValidateAccessToken([FromBody] AccessTokenModel accessTokenModel)
        {
            if (string.IsNullOrEmpty(accessTokenModel.AccessToken))
            {
                return BadRequest("Access token is missing");
            }

            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes(configuration["JwtConfig:Secret"]);

            try
            {
                var validationParameters = new TokenValidationParameters
                {
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(key),
                    ValidateIssuer = false,
                    ValidateAudience = false,
                    ClockSkew = TimeSpan.Zero
                };

                tokenHandler.ValidateToken(accessTokenModel.AccessToken, validationParameters, out SecurityToken validatedToken);

                var jwtToken = validatedToken as JwtSecurityToken;
                if (jwtToken != null)
                {
                    var idClaim = jwtToken.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Sub)?.Value;
                    var usernameClaim = jwtToken.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Name)?.Value;
                    var emailClaim = jwtToken.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Email)?.Value;
                    var specialisationClaim = jwtToken.Claims.FirstOrDefault(c => c.Type == "Specialisation")?.Value;

                    UserInfo userInfo = new UserInfo
                    {
                        Id = idClaim,
                        Name = usernameClaim,
                        Email = emailClaim,
                        SpecialisationName = specialisationClaim
                    };

                    return Ok(userInfo);
                }

                return BadRequest("Invalid access token");
            }
            catch
            {
                return BadRequest("Invalid access token");
            }
        }

        [HttpPost("Refresh")]
        public async Task<IActionResult> RefreshToken()
        {
            var refreshToken = Request.Cookies["RefreshToken"];
            if (string.IsNullOrEmpty(refreshToken))
            {
                return BadRequest("Refresh token is missing");
            }

            var refreshTokenModel = await refreshTokenService.GetRefreshTokenAsync(refreshToken);
            if (refreshTokenModel == null || refreshTokenModel.IsExpired || refreshTokenModel.IsRevoked)
            {
                return BadRequest("Invalid refresh token");
            }

            var user = await userService.GetUserAsync(refreshTokenModel.UserId);
            if (user == null)
            {
                return BadRequest("Invalid user");
            }

            var newAccessToken = await GenerateAccessToken(user.Email);
            var newRefreshToken = GenerateRefreshToken();

            refreshTokenModel.Token = newRefreshToken;

            await refreshTokenService.UpdateRefreshTokenAsync(refreshToken, refreshTokenModel);

            var cookieOptions = new CookieOptions
            {
                HttpOnly = true,
                Secure = false,
                SameSite = SameSiteMode.None,
                Expires = refreshTokenModel.ExpiresAt
            };
            Response.Cookies.Append("RefreshToken", newRefreshToken, cookieOptions);

            return Ok(new { AccessToken = newAccessToken });
        }

        [HttpPost("Revoke")]
        public async Task<IActionResult> Revoke()
        {
            var refreshToken = Request.Cookies["RefreshToken"];
            if (string.IsNullOrEmpty(refreshToken))
            {
                return BadRequest("Refresh token is missing");
            }

            var result = await refreshTokenService.RevokeRefreshTokenAsync(refreshToken);
            if (!result)
            {
                return BadRequest("Invalid refresh token");
            }

            var cookieOptions = new CookieOptions
            {
                HttpOnly = true,
                Secure = false,
                SameSite = SameSiteMode.None,
                Expires = DateTime.UtcNow.AddYears(-1)
            };
            Response.Cookies.Append("RefreshToken", "", cookieOptions);

            return Ok("Refresh token revoked");
        }

        private async Task<string> GenerateAccessToken(string userEmail)
        {
            var user = await userService.GetUserByEmailAsync(userEmail);

            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.ASCII.GetBytes(configuration["JwtConfig:Secret"]);
            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(new Claim[]
                {
                    new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
                    new Claim(JwtRegisteredClaimNames.Name, user.Username),
                    new Claim(JwtRegisteredClaimNames.Email, user.Email),
                    new Claim("Specialisation", user.Specialisation.Name)
                }),
                Expires = DateTime.UtcNow.AddHours(1),
                SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
            };

            var token = tokenHandler.CreateToken(tokenDescriptor);
            return tokenHandler.WriteToken(token);
        }

        private string GenerateRefreshToken()
        {
            return Guid.NewGuid().ToString();
        }
    }
}