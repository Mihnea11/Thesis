namespace Bridge.Models
{
    public class UploadSessionModel
    {
        public string UserId { get; set; }
        public int TotalFiles { get; set; }
        public int FilesUploaded { get; set; }
        public string SessionId { get; set; }

        public UploadSessionModel()
        {
            UserId = string.Empty;
            TotalFiles = 0;
            FilesUploaded = 0;
            SessionId = string.Empty;
        }
    }
}
