//
//  WeeklyPlanView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI

struct WeeklyPlanView: View {
    let week = WorkoutLoader.loadWorkoutData()

    var body: some View {
        NavigationView {
            List(week) { day in
                NavigationLink(destination: WorkoutDetailView(day: day)) {
                    Text(day.day)
                }
            }
            .navigationTitle("Weekly Plan")
        }
    }
}
