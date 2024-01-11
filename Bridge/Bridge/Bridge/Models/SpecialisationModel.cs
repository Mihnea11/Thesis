namespace Bridge.Models
{
    public class SpecialisationModel
    {
        public Guid? Id { get; set; }
        public string Name { get; set; }

        public SpecialisationModel() 
        {
            Name = string.Empty;
        }
    }
}
