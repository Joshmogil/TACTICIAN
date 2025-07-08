//
//  ContentView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//
import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            WeeklyPlanView()
                .tabItem {
                    Label("Workouts", systemImage: "calendar")
                }

            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.crop.circle")
                }
        }
    }
}
