//
//  ExerciseRow.swift
//  groove
//
//  Created by Joshua Mogil on 7/31/25.
//

import SwiftUI


// --- ExerciseRow View ---
struct ExerciseRow: View {
    @Binding var exercise: Exercise

    var body: some View {
        HStack(alignment: .bottom, spacing: 16) {
                Text(exercise.exercise)
                    .font(.headline)
                }
            }
        }

#Preview {
    @Previewable @State var sample = ModelData().workouts[0].workout[0]
    return ExerciseRow(exercise: $sample)
}
