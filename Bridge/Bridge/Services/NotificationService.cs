using Bridge.Contexts;
using Bridge.Hubs;
using Bridge.Models;
using Microsoft.AspNetCore.SignalR;
using MongoDB.Driver;

namespace Bridge.Services
{
    public class NotificationService
    {
        private readonly IMongoCollection<NotificationModel> notifications;
        private readonly IHubContext<NotificationHub> hubContext;

        public NotificationService(MongoDBContext context, IHubContext<NotificationHub> hubContext)
        {
            notifications = context.Notifications;
            this.hubContext = hubContext;
        }

        public async Task AddNotificationAsync(NotificationModel notification)
        {
            await notifications.InsertOneAsync(notification);
            await hubContext.Clients.User(notification.UserId.ToString()).SendAsync("ReceiveNotification", notification);
        }

        public async Task<NotificationModel> GetNotificationAsync(Guid id)
        {
            return await notifications.Find(n => n.Id == id).FirstOrDefaultAsync();
        }

        public async Task<List<NotificationModel>> GetUserNotificationsAsync(string userId)
        {
            return await notifications.Find(n => n.UserId == userId).ToListAsync();
        }

        public async Task<bool> UpdateNotificationAsync(Guid id, NotificationModel updatedNotification)
        {
            var result = await notifications.ReplaceOneAsync(n => n.Id == id, updatedNotification);
            return result.IsAcknowledged && result.ModifiedCount > 0;
        }

        public async Task<bool> DeleteNotificationAsync(Guid id)
        {
            var result = await notifications.DeleteOneAsync(n => n.Id == id);
            return result.IsAcknowledged && result.DeletedCount > 0;
        }

        public async Task<bool> MarkNotificationAsReadAsync(Guid id)
        {
            var update = Builders<NotificationModel>.Update.Set(n => n.IsRead, true);
            var result = await notifications.UpdateOneAsync(n => n.Id == id, update);
            return result.IsAcknowledged && result.ModifiedCount > 0;
        }

        public async Task<bool> DeleteUserNotificationsAsync(string userId)
        {
            var result = await notifications.DeleteManyAsync(n => n.UserId == userId);
            return result.IsAcknowledged && result.DeletedCount > 0;
        }
    }
}