import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-confirmation-dialog',
  templateUrl: './confirmation-dialog.component.html',
  styleUrls: ['./confirmation-dialog.component.scss']
})
export class ConfirmationDialogComponent {
  visible = false;
  message = '';

  @Output() onConfirm = new EventEmitter<void>();
  @Output() onCancel = new EventEmitter<void>();

  show(message: string) {
    this.message = message;
    this.visible = true;
  }

  confirm() {
    this.visible = false;
    this.onConfirm.emit();
  }

  cancel() {
    this.visible = false;
    this.onCancel.emit();
  }
}
