using Bridge.Models;
using MongoDB.Driver;

namespace Bridge.Contexts
{
    public class MongoDBContext
    {
        private readonly IMongoDatabase database;

        public MongoDBContext(IConfiguration configuration)
        {
            var client = new MongoClient(configuration["MongoDB:ConnectionString"]);
            database = client.GetDatabase(configuration["MongoDB:DatabaseName"]);
        }

        public IMongoCollection<UserModel> Users => database.GetCollection<UserModel>("Users");
        public IMongoCollection<SpecialisationModel> Specialisations => database.GetCollection<SpecialisationModel>("Specialisations");
        public IMongoCollection<RefreshTokenModel> RefreshTokens => database.GetCollection<RefreshTokenModel>("RefreshTokens");

    }
}
