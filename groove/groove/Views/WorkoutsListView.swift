import SwiftUI

struct WorkoutsListView: View {
    @StateObject private var model = ModelData()

    var body: some View {
        List {
            ForEach($model.workouts) { $workout in
                Section(header: Text(workout.day)) {
                    WorkoutView(workout: $workout)
                }
            }
        }
    }
}

#Preview {
    WorkoutsListView()
}
