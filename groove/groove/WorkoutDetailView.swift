//
//  WorkoutDetailView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI
struct WorkoutDetailView: View {
    let day: WorkoutDay

    var body: some View {
        List {
            ForEach(groupedExercises(day.workout), id: \.0) { (exercise, sets) in
                Section(header: Text(exercise)) {
                    ForEach(sets, id: \.self) { set in
                        ExerciseRow(set: set)
                    }
                }
            }
        }
        .navigationTitle(day.day)
    }

    func groupedExercises(_ workout: [ExerciseSet]) -> [(String, [ExerciseSet])] {
        var result: [(String, [ExerciseSet])] = []
        var currentExercise: String? = nil
        var currentGroup: [ExerciseSet] = []

        for set in workout {
            if set.exercise != currentExercise {
                if let exercise = currentExercise {
                    result.append((exercise, currentGroup))
                }
                currentExercise = set.exercise
                currentGroup = [set]
            } else {
                currentGroup.append(set)
            }
        }

        if let exercise = currentExercise {
            result.append((exercise, currentGroup))
        }

        return result
    }
}
