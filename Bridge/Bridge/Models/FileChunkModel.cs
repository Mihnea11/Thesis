namespace Bridge.Models
{
    public class FileChunkModel
    {
        public string Label { get; set; }
        public IFormFile ChunkFile { get; set; }
        public string FileName { get; set; }
        public int ChunkIndex { get; set; }
        public int TotalChunks { get; set; }

        public FileChunkModel()
        {
            Label = string.Empty;
            FileName = string.Empty;
            ChunkIndex = 0;
            TotalChunks = 0;
        }
    }
}
