using Bridge.Contexts;
using Bridge.Models;
using MongoDB.Driver;
using System;
using System.Threading.Tasks;

namespace Bridge.Services
{
    public class TokenService
    {
        private readonly IMongoCollection<RefreshTokenModel> refreshTokens;

        public TokenService(MongoDBContext context)
        {
            refreshTokens = context.RefreshTokens;
        }

        public async Task AddRefreshTokenAsync(RefreshTokenModel refreshToken)
        {
            await refreshTokens.InsertOneAsync(refreshToken);
        }

        public async Task<RefreshTokenModel> GetRefreshTokenAsync(string token)
        {
            return await refreshTokens.Find(rt => rt.Token == token).FirstOrDefaultAsync();
        }

        public async Task<bool> UpdateRefreshTokenAsync(string token, RefreshTokenModel updatedRefreshToken)
        {
            var result = await refreshTokens.ReplaceOneAsync(rt => rt.Token == token, updatedRefreshToken);
            return result.IsAcknowledged && result.ModifiedCount > 0;
        }

        public async Task<bool> RevokeRefreshTokenAsync(string token)
        {
            var refreshToken = await GetRefreshTokenAsync(token);
            if (refreshToken != null)
            {
                refreshToken.IsRevoked = true;
                return await UpdateRefreshTokenAsync(token, refreshToken);
            }
            return false;
        }

        public async Task<bool> DeleteRefreshTokenAsync(string token)
        {
            var result = await refreshTokens.DeleteOneAsync(rt => rt.Token == token);
            return result.IsAcknowledged && result.DeletedCount > 0;
        }
    }
}
