import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { SignInComponent } from './components/user-authentication/sign-in/sign-in.component';
import { SignUpComponent } from './components/user-authentication/sign-up/sign-up.component';
import { MatToolbarModule } from '@angular/material/toolbar'; 
import { MatTabsModule } from '@angular/material/tabs'; 
import { MatCardModule } from '@angular/material/card'; 
import { MatFormFieldModule } from '@angular/material/form-field'; 
import { MatCheckboxModule } from '@angular/material/checkbox'; 
import { MatButtonModule } from '@angular/material/button'; 
import { MatInputModule } from '@angular/material/input'
import { MatIconModule } from '@angular/material/icon'; 
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select'; 
import { MatAutocompleteModule } from '@angular/material/autocomplete'; 
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; 
import { TokenInterceptor } from './interceptors/token.interceptor';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { MatMenuModule } from '@angular/material/menu'; 
import { MatSidenavModule } from '@angular/material/sidenav';
import { AppShellComponent } from './components/user-features/app-shell/app-shell.component';
import { HomeComponent } from './components/user-features/home/home.component';
import { UploadDataComponent } from './components/user-features/upload-data/upload-data.component';
import { ProfileComponent } from './components/user-features/profile/profile.component'; 
import { MatListModule } from '@angular/material/list'; 
import { MatProgressBarModule } from '@angular/material/progress-bar'; 
import { NgxDropzoneModule } from 'ngx-dropzone';
import { ModelConfigurationComponent } from './components/user-features/model-configuration/model-configuration.component';
import { ResultsDisplayComponent } from './components/user-features/results-display/results-display.component';
import { ScrollingModule } from '@angular/cdk/scrolling';

@NgModule({
  declarations: [
    AppComponent,
    SignInComponent,
    SignUpComponent,
    AppShellComponent,
    HomeComponent,
    UploadDataComponent,
    ProfileComponent,
    ModelConfigurationComponent,
    ResultsDisplayComponent
  ],
  imports: [
    FormsModule,
    MatIconModule,
    BrowserModule,
    MatTabsModule,
    MatCardModule,
    MatMenuModule,
    MatListModule,
    MatInputModule,
    MatSelectModule,
    ScrollingModule,
    MatButtonModule,
    MatSidenavModule,
    HttpClientModule,
    AppRoutingModule,
    MatToolbarModule,
    NgxDropzoneModule,
    MatCheckboxModule,
    MatFormFieldModule,
    ReactiveFormsModule,
    MatProgressBarModule,
    MatAutocompleteModule,
    BrowserAnimationsModule,
    MatProgressSpinnerModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: TokenInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
