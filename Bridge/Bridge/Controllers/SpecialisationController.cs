using Bridge.Models;
using Bridge.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading.Tasks;

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class SpecialisationController : ControllerBase
    {
        private readonly SpecialisationService specialisationService;

        public SpecialisationController(SpecialisationService specialisationService)
        {
            this.specialisationService = specialisationService;
        }

        [HttpPost]
        public async Task<IActionResult> AddSpecialisation([FromBody] SpecialisationModel specialisation)
        {
            if (specialisation == null)
            {
                return BadRequest("Specialisation data is required");
            }

            try
            {
                var existingSpecialisation = await specialisationService.GetSpecialisationByNameAsync(specialisation.Name);
                if (existingSpecialisation != null)
                {
                    return Conflict("A specialisation with the same name already exists");
                }

                if (specialisation.Id == null)
                {
                    specialisation.Id = Guid.NewGuid();
                }

                await specialisationService.AddSpecialisationAsync(specialisation);
                return CreatedAtAction(nameof(GetSpecialisation), new { id = specialisation.Id }, specialisation);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred while adding the specialisation", error = ex.Message });
            }
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetSpecialisation(Guid id)
        {
            try
            {
                var specialisation = await specialisationService.GetSpecialisationAsync(id);
                if (specialisation == null)
                {
                    return NotFound();
                }

                return Ok(specialisation);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred while retrieving the specialisation", error = ex.Message });
            }
        }

        [HttpGet("By {name}")]
        public async Task<IActionResult> GetSpecialisationByName(string name)
        {
            try
            {
                var specialisation = await specialisationService.GetSpecialisationByNameAsync(name);
                if (specialisation == null)
                {
                    return NotFound();
                }

                return Ok(specialisation);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred while retrieving the specialisation", error = ex.Message });
            }
        }

        [HttpGet]
        public async Task<IActionResult> GetAllSpecialisations()
        {
            try
            {
                var specialisations = await specialisationService.GetAllSpecialisationsAsync();
                return Ok(specialisations);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred while retrieving all specialisations", error = ex.Message });
            }
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateSpecialisation(Guid id, [FromBody] SpecialisationModel specialisation)
        {
            if (specialisation == null)
            {
                return BadRequest("Specialisation data is required");
            }

            try
            {
                var result = await specialisationService.UpdateSpecialisationAsync(id, specialisation);
                if (!result)
                {
                    return NotFound("Specialisation not found");
                }

                return Ok("Specialisation updated successfully");
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred while updating the specialisation", error = ex.Message });
            }
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteSpecialisation(Guid id)
        {
            try
            {
                var result = await specialisationService.DeleteSpecialisationAsync(id);
                if (!result)
                {
                    return NotFound("Specialisation not found");
                }

                return Ok("Specialisation deleted successfully");
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, new { message = "An error occurred while deleting the specialisation", error = ex.Message });
            }
        }
    }
}