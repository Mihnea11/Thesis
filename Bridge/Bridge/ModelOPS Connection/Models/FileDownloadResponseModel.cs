using System.Text.Json.Serialization;

namespace Bridge.ModelOPS_Connection.Models
{
    public class FileDownloadResponseModel
    {
        [JsonPropertyName("message")]
        public string Message { get; set; }

        [JsonPropertyName("file_path")]
        public string FilePath { get; set; }

        public FileDownloadResponseModel() 
        {
            Message = string.Empty;
            FilePath = string.Empty;
        }
    }
}
