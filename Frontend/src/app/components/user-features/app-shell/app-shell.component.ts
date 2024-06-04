import { Component, ElementRef, OnInit, AfterViewInit, Renderer2, ViewChild, HostListener } from '@angular/core';
import { Router } from '@angular/router';
import * as signalR from '@microsoft/signalr';
import { HubConnection, HubConnectionBuilder } from '@microsoft/signalr';
import { Notification } from 'src/app/models/notification';
import { NotificationService } from 'src/app/services/notification.service';
import { TokenService } from 'src/app/services/token.service';
import { UserInfo } from 'src/app/utility/user-info';

@Component({
  selector: 'app-app-shell',
  templateUrl: './app-shell.component.html',
  styleUrls: ['./app-shell.component.scss']
})
export class AppShellComponent implements OnInit, AfterViewInit {
  @ViewChild('toolbar', { static: false }) toolbarElement!: ElementRef;
  @ViewChild('sidenav', { static: false }) sidenavElement!: ElementRef;

  userInfo: UserInfo = {id: '', name: '', email: '', specialisationName: ''};
  menuOpened: boolean = false;
  hubConnection: HubConnection | undefined;

  hasNotifications: boolean = false;
  notifications: Notification[] = [];

  constructor(private tokenService: TokenService, 
              private notificationService: NotificationService,
              private router: Router,
              private renderer: Renderer2) {}

  ngOnInit(): void {
    this.checkAccessToken();
    this.startSignalRConnection();
    this.loadNotifications();
  }

  ngAfterViewInit(): void {
    this.updateSidenavTop();
  }

  @HostListener('window:resize')
  onResize() {
    this.updateSidenavTop();
  }

  toggleMenu(): void {
    this.menuOpened = !this.menuOpened;
  }

  profile() {
    this.router.navigate(['profile']);
  }

  navigate(path: string) {
    this.router.navigate([path]);
  }

  logout() {
    this.tokenService.revokeToken().subscribe({
      next: (response) =>{
        console.log(response);
        this.router.navigate(['sign-in'], {replaceUrl: true});
      },
      error: (error) =>{
        console.log(error);
        this.router.navigate(['sign-in']);
      }
    });
  }

  markAsRead(notificationId: string) {
    this.notificationService.markNotificationAsRead(notificationId).subscribe({
      next: () => {
        this.notifications = this.notifications.filter(notification => notification.id.toString() !== notificationId);
        this.hasNotifications = this.notifications.length > 0;
      },
      error: (error) => console.error('Error marking notification as read:', error)
    });
  }

  private checkAccessToken() {
    const accessTokenString = this.tokenService.getAccessToken();

    if (accessTokenString) {
        this.tokenService.validateAccessToken({ accessToken: accessTokenString }).subscribe({
            next: (response) => {
                if (response.status === 200 && response.body) {
                    this.userInfo = response.body;
                } else {
                    this.refreshTokenAndCheckAgain();
                }
            },
            error: (error) => {
                console.log(error.error);
            }
        });
    } 
    else {
        this.refreshTokenAndCheckAgain();
    }
  }

  private refreshTokenAndCheckAgain() {
    this.tokenService.refreshAccessToken().subscribe({
        next: () => {
            this.checkAccessToken();
        },
        error: (error) => {
        }
    });
  }

  private updateSidenavTop(): void {
    if (this.toolbarElement && this.toolbarElement.nativeElement) {
      const toolbarHeight = this.toolbarElement.nativeElement.offsetHeight;
      this.renderer.setStyle(this.sidenavElement.nativeElement, 'top', `${toolbarHeight}px`);
    }
  }

  private loadNotifications(): void {
    this.notificationService.getNotifications().subscribe({
      next: (notifications) => {
        this.notifications = notifications.filter(notification => !notification.isRead);
        this.hasNotifications = this.notifications.length > 0;
      },
      error: (error) => console.error('Error fetching notifications', error)
    });
  }

  private startSignalRConnection(): void {
    const hubUrl = 'https://localhost:7010/notifications';

    this.hubConnection = new HubConnectionBuilder()
                        .withUrl(hubUrl, { accessTokenFactory: () => this.tokenService.getAccessToken() || '' })
                        .configureLogging(signalR.LogLevel.Information)
                        .withAutomaticReconnect()
                        .build();

    this.hubConnection.start()
                      .then(() => console.log('Connection started'))
                      .catch(err => console.error('Error while starting connection: ' + err));

    this.hubConnection.on('ReceiveNotification', (message) => {
      this.hasNotifications = true;
      this.loadNotifications();
    })
  }
}
