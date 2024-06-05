import { Component, ViewChild } from '@angular/core';
import { Label } from 'src/app/models/label';
import { FileService } from 'src/app/services/file.service';
import { ConfirmationDialogComponent } from 'src/app/dialogs/confirmation-dialog/confirmation-dialog.component';
import { NotificationService } from 'src/app/services/notification.service';
import { Notification } from 'src/app/models/notification';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent {
  labels: Label[] = [];
  private labelToDelete: Label | null = null;
  private fileToDelete: { label: Label, file: string } | null = null;

  notifications: Notification[] = [];

  @ViewChild('confirmationDialog') confirmationDialog!: ConfirmationDialogComponent;

  constructor(private fileService: FileService, private notificationService: NotificationService) {}

  ngOnInit() {
    this.loadLabels();
    this.loadNotifications();
  }

  loadLabels() {
    this.fileService.getLabels().subscribe(labels => {
      this.labels = labels.map(label => ({ name: label, showFiles: false, files: [] }));
    });
  }

  loadNotifications() {
    this.notificationService.getNotifications().subscribe(notifications => {
      this.notifications = notifications;
    });
  }

  toggleFiles(label: Label) {
    if (!label.showFiles) {
      this.fileService.listFiles(label.name).subscribe(files => {
        label.files = files.map(file => this.extractFileName(file));
        label.showFiles = true;
      });
    } else {
      label.showFiles = false;
    }
  }

  extractFileName(filePath: string): string {
    return filePath.split('/').pop() || '';
  }

  showDeleteLabelConfirmation(label: Label) {
    this.labelToDelete = label;
    this.confirmationDialog.show(`Are you sure you want to delete the label ${label.name}?`);
  }

  showDeleteFileConfirmation(label: Label, file: string) {
    this.fileToDelete = { label, file };
    this.confirmationDialog.show(`Are you sure you want to delete the file ${file}?`);
  }

  showDeleteAllConfirmation() {
    this.confirmationDialog.show(`Are you sure you want to delete all labels?`);
  }

  handleConfirm() {
    if (this.labelToDelete) {
      this.deleteLabel(this.labelToDelete);
      this.labelToDelete = null;
    } else if (this.fileToDelete) {
      this.deleteFile(this.fileToDelete.label, this.fileToDelete.file);
      this.fileToDelete = null;
    } else {
      this.deleteAllLabels();
    }
  }

  handleCancel() {
    this.labelToDelete = null;
    this.fileToDelete = null;
  }

  deleteLabel(label: Label) {
    this.fileService.deleteLabelDirectory(label.name).subscribe(() => {
      this.labels = this.labels.filter(l => l !== label);
    });
  }

  deleteFile(label: Label, file: string) {
    this.fileService.deleteFileByName(label.name, file).subscribe(() => {
      label.files = label.files.filter(f => f !== file);
    });
  }

  deleteAllLabels() {
    this.labels.forEach(label => {
      this.fileService.deleteLabelDirectory(label.name).subscribe(() => {
        this.labels = this.labels.filter(l => l !== label);
      });
    });
  }

  deleteNotification(notification: Notification) {
    this.notificationService.deleteNotification(notification.id.toString()).subscribe(() => {
      this.notifications = this.notifications.filter(n => n !== notification);
    });
  }

  clearAllNotifications() {
    this.notifications.forEach(notification => {
      this.notificationService.deleteNotification(notification.id.toString()).subscribe(() => {
        this.notifications = this.notifications.filter(n => n !== notification);
      });
    });
  }
}
