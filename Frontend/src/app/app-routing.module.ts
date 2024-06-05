import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { tokenGuard } from './guards/token.guard';
import { AppShellComponent } from './components/user-features/app-shell/app-shell.component';
import { HomeComponent } from './components/user-features/home/home.component';
import { UploadDataComponent } from './components/user-features/upload-data/upload-data.component';
import { ProfileComponent } from './components/user-features/profile/profile.component';
import { SignInComponent } from './components/user-authentication/sign-in/sign-in.component';
import { SignUpComponent } from './components/user-authentication/sign-up/sign-up.component';
import { ModelConfigurationComponent } from './components/user-features/model-configuration/model-configuration.component';
import { ResultsDisplayComponent } from './components/user-features/results-display/results-display.component';
import { SettingsComponent } from './components/user-features/settings/settings.component';

const routes: Routes = [
  { path: 'sign-in', component: SignInComponent },
  { path: 'sign-up', component: SignUpComponent },
  {
    path: '', 
    component: AppShellComponent,
    canActivate: [tokenGuard],
    children: [
      { path: 'profile', component: ProfileComponent},
      { path: 'settings', component: SettingsComponent},
      { path: 'home', component: HomeComponent },
      { path: 'upload-data', component: UploadDataComponent},
      { path: 'configure-model', component: ModelConfigurationComponent},
      { path: 'results', component: ResultsDisplayComponent},
      { path: '', redirectTo: 'home', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: 'authentication' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
