import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Specialisation } from 'src/app/models/specialisation';
import { User } from 'src/app/models/user';
import { AuthenticationService } from 'src/app/services/authentication.service';
import { SpecialisationService } from 'src/app/services/specialisation.service';

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.scss']
})
export class SignUpComponent {
  name: string = '';
  lastname: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  specialisation: Specialisation = { id: null, name: '' };
  
  specialisations: Specialisation[] = [];
  filteredSpecialisations: Specialisation[] = [];

  hidePassword = true;
  hideConfirmPassword = true;

  hasSuccess: boolean = false;
  successMessage: string = '';
  hasError: boolean = false;
  errorMessage: string = '';

  closingDropdown: boolean = false;
  openDropdown: boolean = false;
  isLoading: boolean = false;

  constructor(private authenticationService: AuthenticationService,
              private specialisationService: SpecialisationService,
              private router: Router) {
    this.getAllSpecialisations();
  }

  onSubmit() {
    this.hasSuccess = false;
    this.hasError = false;
    this.successMessage = '';
    this.errorMessage = '';

    if (this.validateInput()) {
      this.isLoading = true;

      let userData: User = {
        id: null,
        username: this.name + ' ' + this.lastname,
        email: this.email,
        password: this.password,
        specialisation: this.specialisation
      };

      this.authenticationService.registerUser(userData).subscribe({
        next: (response) => {
          this.isLoading = false;
          this.hasSuccess = true;
          this.successMessage = response.message;

          this.router.navigate(['/sign-in']);
        },
        error: (error: HttpErrorResponse) => {
          this.isLoading = false;
          this.hasError = true;
          this.errorMessage = error.error || "An unknown error occurred.";
        }
      });
    }
  }

  filterSpecialisations() {
    const filterValue = this.specialisation.name.toLowerCase();
    this.filteredSpecialisations = this.specialisations.filter(spec =>
      spec.name.toLowerCase().includes(filterValue)
    );
    this.filteredSpecialisations = this.filteredSpecialisations.filter(spec =>
      spec.name.toLowerCase() !== filterValue
    );
  }

  selectSpecialisation(spec: Specialisation) {
    this.specialisation = spec;
    this.closeDropdown();
  }

  closeDropdown() {
    this.closingDropdown = true;
    setTimeout(() => {
      this.openDropdown = false;
      this.closingDropdown = false;
    }, 300);
  }

  private getAllSpecialisations(): void {
    this.specialisationService.getAllSpecialisations().subscribe({
      next: (specialisations) => {
        this.specialisations = specialisations;
        this.filteredSpecialisations = specialisations;
      },
      error: (error: HttpErrorResponse) => {
        console.error('Error fetching specialisations', error);
      }
    });
  }

  private validateInput() {
    this.hasError = false;
    this.errorMessage = '';
    
    if (this.name === '') {
      this.hasError = true;
      this.errorMessage = 'First name cannot be empty!';
      return false;
    }

    if (this.lastname === '') {
      this.hasError = true;
      this.errorMessage = 'Last name cannot be empty';
      return false;
    }

    if (this.email === '') {
      this.hasError = true;
      this.errorMessage = 'Email cannot be empty';
      return false;
    } else {
      let emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
      if (!emailPattern.test(this.email)) {
        this.hasError = true;
        this.errorMessage = 'Invalid email format';
        return false;
      }
    }

    if (this.password === '') {
      this.hasError = true;
      this.errorMessage = 'Password cannot be empty';
      return false;
    } else {
      let hasUppercase = /[A-Z]/.test(this.password);
      let hasLowercase = /[a-z]/.test(this.password);
      let hasNumeric = /[0-9]/.test(this.password);
      let hasSpecialCharacter = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]+/.test(this.password);
      if (this.password.length < 8 || !hasUppercase || !hasLowercase || !hasNumeric || !hasSpecialCharacter) {
        this.hasError = true;
        this.errorMessage = 'Password must meet the following requirements:';
        if (this.password.length < 8) this.errorMessage += '<br>- At least 8 characters long';
        if (!hasUppercase) this.errorMessage += '<br>- Contains at least one uppercase letter';
        if (!hasLowercase) this.errorMessage += '<br>- Contains at least one lowercase letter';
        if (!hasNumeric) this.errorMessage += '<br>- Contains at least one number';
        if (!hasSpecialCharacter) this.errorMessage += '<br>- Contains at least one special character (e.g., !@#$%^&*())';
        return false;
      }
    }

    if (this.confirmPassword === '') {
      this.hasError = true;
      this.errorMessage = "Confirm password cannot be empty";
      return false;
    }

    if (this.password !== this.confirmPassword) {
      this.hasError = true;
      this.errorMessage = "Password and Confirm Password fields must match";
      return false;
    }

    if (this.specialisation.name === '') {
      this.hasError = true;
      this.errorMessage = "Specialisation cannot be empty";
      return false;
    }
    else {
      const specialisationExists = this.specialisations.some(spec => 
        spec.name.toLowerCase() === this.specialisation.name.toLowerCase()
      );
  
      if (!specialisationExists) {
        this.hasError = true;
        this.errorMessage = "Please select a valid specialisation";
        return false;
      }
    }

    return true;
  }
}
