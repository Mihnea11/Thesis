using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Bson;

namespace Bridge.Models
{
    public class RefreshTokenModel
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string? Id { get; set; }

        public string Token { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime ExpiresAt { get; set; }
        public Guid UserId { get; set; }
        public bool IsExpired => DateTime.UtcNow >= ExpiresAt;
        public bool IsRevoked { get; set; }

        public RefreshTokenModel() 
        {
            Token = string.Empty;
        }
    }
}
