import SwiftUI

struct ContentView: View {
    @StateObject private var model = ModelData()
    @State private var selection: Tab = .home

    enum Tab {
        case home
        case current
    }

    var body: some View {
        NavigationStack {
            TabView(selection: $selection) {
                WorkoutsListView()
                    .tag(Tab.home)
                    .tabItem { Label("Home", systemImage: "house") }

                CurrentWorkoutView()
                    .tag(Tab.current)
                    .tabItem { Label("Workout", systemImage: "dumbbell") }
            }
            .toolbar {
                NavigationLink(destination: Profile()) {
                    Image(systemName: "person.crop.circle")
                }
            }
            .navigationTitle("Groove")
        }
        .environmentObject(model)
    }
}

#Preview {
    ContentView()
}
