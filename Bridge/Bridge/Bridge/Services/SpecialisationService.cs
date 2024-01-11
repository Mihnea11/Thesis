using Bridge.Contexts;
using Bridge.Models;
using MongoDB.Driver;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Bridge.Services
{
    public class SpecialisationService
    {
        private readonly IMongoCollection<SpecialisationModel> specialisations;

        public SpecialisationService(MongoDBContext context)
        {
            specialisations = context.Specialisations;
        }

        public async Task AddSpecialisationAsync(SpecialisationModel specialisation)
        {
            await specialisations.InsertOneAsync(specialisation);
        }

        public async Task<SpecialisationModel> GetSpecialisationAsync(Guid id)
        {
            return await specialisations.Find(s => s.Id == id).FirstOrDefaultAsync();
        }

        public async Task<SpecialisationModel> GetSpecialisationByNameAsync(string name)
        {
            return await specialisations.Find(s => s.Name == name).FirstOrDefaultAsync();
        }

        public async Task<List<SpecialisationModel>> GetAllSpecialisationsAsync()
        {
            return await specialisations.Find(_ => true).ToListAsync();
        }

        public async Task<bool> UpdateSpecialisationAsync(Guid id, SpecialisationModel updatedSpecialisation)
        {
            var result = await specialisations.ReplaceOneAsync(s => s.Id == id, updatedSpecialisation);
            return result.IsAcknowledged && result.ModifiedCount > 0;
        }

        public async Task<bool> DeleteSpecialisationAsync(Guid id)
        {
            var result = await specialisations.DeleteOneAsync(s => s.Id == id);
            return result.IsAcknowledged && result.DeletedCount > 0;
        }
    }
}
