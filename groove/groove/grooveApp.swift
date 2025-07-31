import SwiftUI

struct ContentView: View {
    var body: some View {
        WorkoutsListView()
    }
}

#Preview {
    ContentView()
}

@main
struct grooveApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
