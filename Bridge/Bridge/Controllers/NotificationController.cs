using Bridge.Models;
using Bridge.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace Bridge.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class NotificationController : ControllerBase
    {
        private readonly NotificationService notificationService;

        public NotificationController(NotificationService notificationService)
        {
            this.notificationService = notificationService;
        }

        [HttpPost]
        public async Task<IActionResult> AddNotification([FromBody] NotificationModel notification)
        {
            await notificationService.AddNotificationAsync(notification);
            return CreatedAtAction(nameof(GetNotification), new { id = notification.Id }, notification);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetNotification(Guid id)
        {
            var notification = await notificationService.GetNotificationAsync(id);
            if (notification == null)
            {
                return NotFound();
            }
            return Ok(notification);
        }

        [HttpGet]
        public async Task<IActionResult> GetUserNotifications()
        {
            var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId == null)
            {
                return BadRequest("No user identifier found");
            }

            var notifications = await notificationService.GetUserNotificationsAsync(userId);
            return Ok(notifications);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateNotification(Guid id, [FromBody] NotificationModel updatedNotification)
        {
            var result = await notificationService.UpdateNotificationAsync(id, updatedNotification);
            if (!result)
            {
                return NotFound();
            }
            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteNotification(Guid id)
        {
            var result = await notificationService.DeleteNotificationAsync(id);
            if (!result)
            {
                return NotFound();
            }
            return NoContent();
        }

        [HttpPatch("{id}/read")]
        public async Task<IActionResult> MarkNotificationAsRead(Guid id)
        {
            var result = await notificationService.MarkNotificationAsReadAsync(id);
            if (!result)
            {
                return NotFound();
            }
            return NoContent();
        }
    }
}

