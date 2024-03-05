using Microsoft.AspNetCore.SignalR;

namespace Bridge.Hubs
{
    public class NotificationHub : Hub
    {
        public async Task SendUploadNotification(string user, string message)
        {
            await Clients.User(user).SendAsync("ReceiveMessage", message);
        }

        public async Task SendNotifications(string user, object notification)
        {
            await Clients.User(user).SendAsync("ReceiveNotification", notification);
        }
    }
}
