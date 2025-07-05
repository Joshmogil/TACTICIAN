//
//  WorkoutDay.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import Foundation

struct WorkoutDay: Codable, Identifiable {
    var id: UUID = UUID()
    let day: String
    let workout: [ExerciseSet]

    private enum CodingKeys: String, CodingKey {
        case day, workout
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.day = try container.decode(String.self, forKey: .day)
        self.workout = try container.decode([ExerciseSet].self, forKey: .workout)
        self.id = UUID() // Generate manually
    }
}

struct ExerciseSet: Codable, Hashable, Identifiable {
    var id: UUID = UUID()
    let exercise: String
    let amount: Double
    let actualAmount: Double
    let amountUnit: String
    let intensity: Double
    let actualIntensity: Double
    let intensityUnit: String
    let perceivedExertion: String

    private enum CodingKeys: String, CodingKey {
        case exercise, amount, actualAmount, amountUnit,
             intensity, actualIntensity, intensityUnit, perceivedExertion
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.exercise = try container.decode(String.self, forKey: .exercise)
        self.amount = try container.decode(Double.self, forKey: .amount)
        self.actualAmount = try container.decode(Double.self, forKey: .actualAmount)
        self.amountUnit = try container.decode(String.self, forKey: .amountUnit)
        self.intensity = try container.decode(Double.self, forKey: .intensity)
        self.actualIntensity = try container.decode(Double.self, forKey: .actualIntensity)
        self.intensityUnit = try container.decode(String.self, forKey: .intensityUnit)
        self.perceivedExertion = try container.decode(String.self, forKey: .perceivedExertion)
        self.id = UUID()
    }
}
