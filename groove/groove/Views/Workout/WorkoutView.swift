import SwiftUI

struct WorkoutView: View {
    @Binding var workout: WorkoutData

    var body: some View {
        List {
            ForEach(workout.workout.indices, id: \.self) { idx in
                ExerciseRow(exercise: $workout.workout[idx]) {
                    workout.workout.remove(at: idx)
                }
            }
        }
    }
}

#Preview {
    @Previewable @State var workout = ModelData().workouts[4]
    return WorkoutView(workout: $workout)
}
