import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { tokenGuard } from './guards/token.guard';
import { AppShellComponent } from './components/user-features/app-shell/app-shell.component';
import { HomeComponent } from './components/user-features/home/home.component';
import { UploadDataComponent } from './components/user-features/upload-data/upload-data.component';
import { ViewPredictionsComponent } from './components/user-features/view-predictions/view-predictions.component';
import { KnowledgeGraphComponent } from './components/user-features/knowledge-graph/knowledge-graph.component';
import { ProfileComponent } from './components/user-features/profile/profile.component';
import { SignInComponent } from './components/user-authentication/sign-in/sign-in.component';
import { SignUpComponent } from './components/user-authentication/sign-up/sign-up.component';

const routes: Routes = [
  { path: 'sign-in', component: SignInComponent },
  { path: 'sign-up', component: SignUpComponent },
  { path: 'profile', component: ProfileComponent, canActivate: [tokenGuard]},
  {
    path: '', 
    component: AppShellComponent,
    children: [
      { path: 'home', component: HomeComponent },
      { path: 'upload-data', component: UploadDataComponent},
      { path: 'predictions', component: ViewPredictionsComponent},
      { path: 'knowledge-graph', component: KnowledgeGraphComponent},
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
