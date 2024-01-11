namespace Bridge.Models
{
    public class UserModel
    {
        public Guid? Id { get; set; }
        public string Username { get; set; }
        public string Email { get; set; }
        public string Password { get; set; }
        public SpecialisationModel Specialisation { get; set; }

        public UserModel() 
        {
            Username = string.Empty;
            Email = string.Empty;
            Password = string.Empty;
            Specialisation = new SpecialisationModel();
        }
    }
}
