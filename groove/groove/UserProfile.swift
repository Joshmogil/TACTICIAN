//
//  UserProfile.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import Foundation

struct Range: Codable, Hashable {
    var start: Int
    var end: Int
}

struct Interest: Identifiable, Codable, Hashable {
    var id = UUID()
    var name: String
    var skill: String
    
    private enum CodingKeys: String, CodingKey {
        case name, skill
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.name = try container.decode(String.self, forKey: .name)
        self.skill = try container.decode(String.self, forKey: .skill)
        self.id = UUID()
    }
}

struct UserProfile: Codable {
    var name: String
    var age: String
    var gender: String
    var activityLevel: Int
    var desiredWorkoutsPerWeek: Range
    var favoriteExercises: [String]
    var interests: [Interest]
}
