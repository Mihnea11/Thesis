import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { TokenService } from 'src/app/services/token.service';
import { UserCredentials } from 'src/app/utility/user-credentials';

@Component({
  selector: 'app-sign-in',
  templateUrl: './sign-in.component.html',
  styleUrls: ['./sign-in.component.scss']
})
export class SignInComponent {
  email: string = '';
  password: string = '';
  rememberMe: boolean = false;

  hidePassword: boolean = true;

  hasError: boolean = false;
  errorMessage: string = '';

  isLoading: boolean = false;

  constructor(private authenticationService: AuthenticationService, 
              private tokenService: TokenService,
              private router: Router) {}

  onSubmit(){
    this.hasError = false;
    this.errorMessage = '';

    if(this.validateInput() == true){
      this.isLoading = true;

      let credentials: UserCredentials = {
        email: this.email,
        password: this.password
      }
  
      this.authenticationService.loginUser(credentials, this.rememberMe).subscribe({
        next: (response) =>{
          this.tokenService.storeAccessToken(response.accessToken);

          this.router.navigate(['/home'], {replaceUrl: true});
        },
        error: (error: HttpErrorResponse) =>{
          this.isLoading = false;
          this.hasError = true;
          this.errorMessage = error.error || "An unknown error occurred.";
        }
      })
    }
  }

  private validateInput(){
    if(this.email == ''){
      this.hasError = true;
      this.errorMessage = "Email cannot be empty";

      return false;
    }

    if(this.password == ''){
      this.hasError = true;
      this.errorMessage = 'Password cannot be empty';

      return false;
    }

    return true;
  }
}
