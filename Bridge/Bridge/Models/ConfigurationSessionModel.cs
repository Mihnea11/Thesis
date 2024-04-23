namespace Bridge.Models
{
    public class ConfigurationSessionModel
    {
        public string UserId { get; set; }
        public string SessionId { get; set; }
        public string TemporaryDirectory { get; set; }
        public string State { get; set; }

        public ConfigurationSessionModel() 
        {
            UserId = string.Empty;
            SessionId = string.Empty;
            TemporaryDirectory = string.Empty;
            State = string.Empty;
        }
    }
}
