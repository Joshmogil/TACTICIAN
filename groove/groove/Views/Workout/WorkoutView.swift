import SwiftUI

struct WorkoutView: View {
    @Binding var workout: Workout

    var body: some View {
        List {
            ForEach($workout.workout) { $exercise in
                ExerciseRow(exercise: $exercise)
            }
        }
    }
}

#Preview {
    @Previewable @State var workout = ModelData().workouts[4]
    return WorkoutView(workout: $workout)
}
