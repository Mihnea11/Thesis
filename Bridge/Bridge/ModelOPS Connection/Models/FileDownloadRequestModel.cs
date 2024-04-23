using System.Text.Json.Serialization;

namespace Bridge.ModelOPS_Connection.Models
{
    public class FileDownloadRequestModel
    {
        [JsonPropertyName("bucket_name")]
        public string BucketName { get; set; }

        [JsonPropertyName("user_id")]
        public string UserId { get; set; }

        [JsonPropertyName("label")]
        public string Label { get; set; }

        public FileDownloadRequestModel()
        {
            BucketName = string.Empty;
            UserId = string.Empty;
            Label = string.Empty;
        }
    }
}
