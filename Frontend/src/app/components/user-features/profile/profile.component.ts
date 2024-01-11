import { Component, OnInit } from '@angular/core';
import { Guid } from 'guid-typescript';
import { User } from 'src/app/models/user';
import { TokenService } from 'src/app/services/token.service';
import { UserInfo } from 'src/app/utility/user-info';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
  userInfo: UserInfo = {name: '', email: '', specialisationName: ''};

  constructor(private tokenService: TokenService) {}

  ngOnInit(): void {
    this.checkAccessToken();
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
}
