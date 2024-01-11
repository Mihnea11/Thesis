import { Component, ElementRef, OnInit, AfterViewInit, Renderer2, ViewChild, HostListener } from '@angular/core';
import { Router } from '@angular/router';
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

  userInfo: UserInfo = {name: '', email: '', specialisationName: ''};
  menuOpened: boolean = false;

  constructor(private tokenService: TokenService, 
              private router: Router,
              private renderer: Renderer2) {}

  ngOnInit(): void {
    this.checkAccessToken();
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

  private checkAccessToken() {
    const accessTokenString = this.tokenService.getAccessToken();

    if (accessTokenString) {
        this.tokenService.validateAccessToken({ accessToken: accessTokenString }).subscribe({
            next: (response) => {
                if (response.status === 200 && response.body) {
                    this.userInfo = response.body;
                    console.log(response.body);
                    console.log(this.userInfo.name);
                    console.log(this.userInfo.email);
                    console.log(this.userInfo.specialisationName);
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
}
