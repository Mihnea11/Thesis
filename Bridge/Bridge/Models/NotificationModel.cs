namespace Bridge.Models
{
    public class NotificationModel
    {
        public Guid Id { get; set; }
        public string UserId { get; set; }
        public string Message { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public bool IsRead { get; set; } = false;

        public NotificationModel() 
        {
            Id = Guid.Empty;
            UserId = string.Empty;
            Message = string.Empty;
        }
    }
}
