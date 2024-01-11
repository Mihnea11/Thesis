using Bridge.Contexts;
using Bridge.Models;
using MongoDB.Driver;
using System.Threading.Tasks;

namespace Bridge.Services
{
    public class UserService
    {
        private readonly IMongoCollection<UserModel> users;

        public UserService(MongoDBContext context)
        {
            users = context.Users;
        }

        public async Task AddUserAsync(UserModel user)
        {
            await users.InsertOneAsync(user);
        }

        public async Task<UserModel> GetUserAsync(Guid id)
        {
            return await users.Find(user => user.Id == id).FirstOrDefaultAsync();
        }

        public async Task<UserModel> GetUserByEmailAsync(string email)
        {
            return await users.Find(user => user.Email == email).FirstOrDefaultAsync();
        }

        public async Task<bool> UpdateUserAsync(Guid id, UserModel updatedUser)
        {
            var result = await users.ReplaceOneAsync(user => user.Id == id, updatedUser);
            return result.IsAcknowledged && result.ModifiedCount > 0;
        }

        public async Task<bool> DeleteUserAsync(Guid id)
        {
            var result = await users.DeleteOneAsync(user => user.Id == id);
            return result.IsAcknowledged && result.DeletedCount > 0;
        }

        public async Task<List<UserModel>> GetAllUsersAsync()
        {
            return await users.Find(_ => true).ToListAsync();
        }
    }
}
