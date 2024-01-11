using Bridge.Models;
using Bridge.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Cryptography.KeyDerivation;
using System.Security.Cryptography;
using Bridge.Utility;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class AuthenticationController : ControllerBase
    {
        private readonly UserService userService;
        private readonly TokenService refreshTokenService;
        private readonly IConfiguration configuration;

        public AuthenticationController(UserService userService, TokenService refreshTokenService, IConfiguration configuration)
        {
            this.userService = userService;
            this.refreshTokenService = refreshTokenService;
            this.configuration = configuration;
        }

        [HttpPost("Register")]
        public async Task<IActionResult> RegisterUser([FromBody] UserModel user)
        {
            if (user == null || !ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            try
            {
                var existingUser = await userService.GetUserByEmailAsync(user.Email);
                if (existingUser != null)
                {
                    return Conflict("Email already used");
                }

                if (user.Id == null)
                {
                    user.Id = Guid.NewGuid();
                }
                user.Password = HashPassword(user.Password);

                await userService.AddUserAsync(user);
                return Ok(new { message = "User registered successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "A server error has occurred", error = ex.Message });
            }
        }

        [HttpPost("Login")]
        public async Task<IActionResult> LoginUser([FromBody] UserCredentials credentials, [FromQuery] bool rememberMe = false)
        {
            if (credentials == null || string.IsNullOrWhiteSpace(credentials.Email) || string.IsNullOrWhiteSpace(credentials.Password))
            {
                return BadRequest("Invalid email or password");
            }

            try
            {
                var user = await userService.GetUserByEmailAsync(credentials.Email);
                if (user == null || !VerifyPassword(credentials.Password, user.Password))
                {
                    return Unauthorized("Invalid email or password");
                }

                var tokenHandler = new JwtSecurityTokenHandler();
                var key = Encoding.ASCII.GetBytes(configuration["JwtConfig:Secret"]);

                var claims = new List<Claim>
                {
                    new Claim(JwtRegisteredClaimNames.Name, user.Username),
                    new Claim(JwtRegisteredClaimNames.Email, user.Email),
                    new Claim("Specialisation", user.Specialisation.Name)
                };

                var accessTokenExpiration = DateTime.UtcNow.AddHours(1);
                var tokenDescriptor = new SecurityTokenDescriptor
                {
                    Subject = new ClaimsIdentity(claims),
                    Expires = accessTokenExpiration,
                    SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
                };

                var accessToken = tokenHandler.CreateToken(tokenDescriptor);
                var accessTokenString = tokenHandler.WriteToken(accessToken);

                var refreshToken = GenerateRefreshToken();
                var refreshTokenModel = new RefreshTokenModel
                {
                    Token = refreshToken,
                    UserId = user.Id!.Value,
                    CreatedAt = DateTime.UtcNow,
                    ExpiresAt = rememberMe ? DateTime.UtcNow.AddDays(30) : DateTime.UtcNow.AddDays(1),
                    IsRevoked = false
                };

                await refreshTokenService.AddRefreshTokenAsync(refreshTokenModel);

                var cookieOptions = new CookieOptions
                {
                    HttpOnly = true,
                    Secure = false,
                    SameSite = SameSiteMode.None,
                    Expires = refreshTokenModel.ExpiresAt
                };
                Response.Cookies.Append("RefreshToken", refreshToken, cookieOptions);

                return Ok(new AccessTokenModel { AccessToken = accessTokenString });
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred", error = ex.Message });
            }
        }

        private string GenerateRefreshToken()
        {
            var randomNumber = new byte[32];
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(randomNumber);
                return Convert.ToBase64String(randomNumber);
            }
        }

        private bool VerifyPassword(string inputPassword, string storedHashWithSalt)
        {
            var parts = storedHashWithSalt.Split(new[] { "||" }, StringSplitOptions.None);
            if (parts.Length != 2)
            {
                throw new InvalidOperationException("Stored hash should contain the salt and hash");
            }

            var salt = Convert.FromBase64String(parts[0]);
            var storedHash = parts[1];

            string hashedInput = Convert.ToBase64String(KeyDerivation.Pbkdf2(
                password: inputPassword,
                salt: salt,
                prf: KeyDerivationPrf.HMACSHA256,
                iterationCount: 10000,
                numBytesRequested: 256 / 8));

            return storedHash == hashedInput;
        }


        private string HashPassword(string password)
        {
            byte[] salt = new byte[128 / 8];
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(salt);
            }

            string hashed = Convert.ToBase64String(KeyDerivation.Pbkdf2(
                password: password,
                salt: salt,
                prf: KeyDerivationPrf.HMACSHA256,
                iterationCount: 10000,
                numBytesRequested: 256 / 8));

            return Convert.ToBase64String(salt) + "||" + hashed;
        }
    }
}