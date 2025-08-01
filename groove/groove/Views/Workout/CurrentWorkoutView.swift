import SwiftUI

struct CurrentWorkoutView: View {
    @EnvironmentObject var model: ModelData

    var body: some View {
        if let index = model.workouts.indices.first {
            WorkoutView(workout: $model.workouts[index])
        } else {
            Text("No Workouts")
        }
    }
}

#Preview {
    CurrentWorkoutView().environmentObject(ModelData())
}
