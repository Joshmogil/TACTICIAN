//
//  ProfileView.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI

struct ProfileView: View {
    // ─────────────────────────── Stored State ───────────────────────────
    @State private var profile: UserProfile = ProfileLoader.loadProfile()
    @Environment(\.editMode) private var editMode

    // “Add Exercise” scratchpad
    @State private var newExercise: String = ""

    // ─────────────────────────── UI ───────────────────────────
    var body: some View {
        NavigationView {
            Form {
                basicsSection           // ← new look
                workoutPreferencesSection
                interestsSection
            }
            .navigationTitle("Your Profile")
        }
    }

    // ────────────────── Basics ──────────────────
    private var basicsSection: some View {
        Section("Basics") {

            // Name
            TextField("Name", text: $profile.name)
                .textInputAutocapitalization(.words)
                .textFieldStyle(.roundedBorder)

            // Age (inline wheel)
            Picker("Age", selection: $profile.age) {
                ForEach(5...115, id: \.self) { age in
                    Text("\(age)").tag(age)
                }
            }
            .pickerStyle(.menu)          // ← compact dropdown, no giant list

            // Gender (segmented)
            Picker("Gender", selection: $profile.gender) {
                ForEach(["male", "female", "other"], id: \.self) { g in
                    Text(g.capitalized).tag(g)
                }
            }
            .pickerStyle(.segmented)

            // Activity Level (menu)
            Picker("Activity Level", selection: $profile.activityLevel) {
                ForEach(["low", "medium", "high", "extreme"], id: \.self) { level in
                    Text(level.capitalized).tag(level)
                }
            }
            .pickerStyle(.menu)
        }
    }

    // ─────────────── Workout Preferences ───────────────
    private var workoutPreferencesSection: some View {
        Section(
            header:
                HStack {
                    Text("Workout Preferences")
                    Spacer()
                    EditButton()
                }
        ) {
            // range selector
            VStack(alignment: .leading, spacing: 8) {
                Text("Workouts/Week:")
                HStack {
                    Stepper("", value: $profile.desiredWorkoutsPerWeek.start, in: 0...7)
                    Text("\(profile.desiredWorkoutsPerWeek.start)")
                    Text("–")
                    Stepper("", value: $profile.desiredWorkoutsPerWeek.end,
                            in: profile.desiredWorkoutsPerWeek.start...7)
                    Text("\(profile.desiredWorkoutsPerWeek.end)")
                }
            }

            // favourite exercises (List kept as you had it)
            List {
                Section("Favorite Exercises") {
                    ForEach(profile.favoriteExercises, id: \.self) { exercise in
                        Text(exercise.capitalized)
                    }
                    .onDelete { idx in
                        profile.favoriteExercises.remove(atOffsets: idx)
                    }

                    HStack {
                        TextField("Add Exercise", text: $newExercise)
                        Button("Add") {
                            let trimmed = newExercise
                                .trimmingCharacters(in: .whitespacesAndNewlines)
                            guard !trimmed.isEmpty, trimmed.count <= 40 else { return }
                            profile.favoriteExercises.append(trimmed)
                            newExercise = ""
                        }
                        .disabled(newExercise.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    }
                }
            }
            .environment(\.editMode, editMode)   // let EditButton drive deletes
        }
    }

    // ─────────────── Interests ───────────────
    private var interestsSection: some View {
        Section("Interests") {
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
}
