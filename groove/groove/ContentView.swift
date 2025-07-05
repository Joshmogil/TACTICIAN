//
//  ContentView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI

struct ContentView: View {
    let week = WorkoutLoader.loadWorkoutData()

    var body: some View {
        NavigationView {
            List(week) { day in
                NavigationLink(destination: WorkoutDetailView(day: day)) {
                    Text(day.day)
                }
            }
            .navigationTitle("Weekly Plan")
            .toolbar {
                NavigationLink(destination: ProfileView()) {
                    Image(systemName: "person.crop.circle")
                        .imageScale(.large)
                }
            }
        }
    }
}
