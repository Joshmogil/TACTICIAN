//
//  Untitled.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import Foundation

class WorkoutLoader {
    static func loadWorkoutData() -> [WorkoutDay] {
        guard let url = Bundle.main.url(forResource: "week_1", withExtension: "json") else {
            fatalError("week_1.json not found")
        }

        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase // <-- this line
            return try decoder.decode([WorkoutDay].self, from: data)
        } catch {
            fatalError("Failed to decode week_1.json: \(error)")
        }
    }
}
