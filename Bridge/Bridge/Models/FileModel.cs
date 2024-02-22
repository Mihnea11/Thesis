namespace Bridge.Models
{
    public class FileModel
    {
        public List<IFormFile> Files { get; set; }
        public string Label { get; set; }

        public FileModel()
        {
            Files = new List<IFormFile>();
            Label = string.Empty;
        }
    }
}
