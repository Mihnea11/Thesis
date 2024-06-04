import { Component, OnInit } from '@angular/core';
import { TokenService } from 'src/app/services/token.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent {
  id: string = '';
  name: string = '';
  email: string = '';
  specialisation: string = '';

  constructor(private tokenService: TokenService) {}

  ngOnInit(): void {
    this.initializeUserProfile();
  }

  private initializeUserProfile() {
    let accessTokenString = this.tokenService.getAccessToken();

    if (accessTokenString) {
      let decodedToken = JSON.parse(window.atob(accessTokenString.split('.')[1]));

      this.id = decodedToken.sub;
      this.name = decodedToken.name;
      this.email = decodedToken.email;
      this.specialisation = decodedToken.Specialisation;
    }
  }
}
