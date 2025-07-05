//
//  ProfileView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI

struct ProfileView: View {
    @State private var profile: UserProfile = ProfileLoader.loadProfile()

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Basics")) {
                    Text("Name: \(profile.name)")
                    Text("Age: \(profile.age)")
                    Text("Gender: \(profile.gender.capitalized)")
                    Text("Activity Level: \(profile.activityLevel)")
                }

                Section(header: Text("Workout Preferences")) {
                    Text("Desired Workouts per Week: \(profile.desiredWorkoutsPerWeek.start)–\(profile.desiredWorkoutsPerWeek.end)")
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Favorite Exercises:")
                            .font(.subheadline)
                        ForEach(profile.favoriteExercises, id: \.self) { exercise in
                            Text("• \(exercise.capitalized)")
                        }
                    }
                }

                Section(header: Text("Interests")) {
                    ForEach(profile.interests) { interest in
                        HStack {
                            Text(interest.name.capitalized)
                            Spacer()
                            Text(interest.skill)
                                .foregroundColor(.gray)
                                .font(.subheadline)
                        }
                    }
                }
            }
            .navigationTitle("Your Profile")
        }
    }
}

