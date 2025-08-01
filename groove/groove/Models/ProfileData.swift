//
//  Profile.swift
//  groove
//
//  Created by Joshua Mogil on 8/1/25.
//


import Foundation

struct Interest: Codable, Hashable, Identifiable{
    var id: UUID { _id ?? UUID()}
    private var _id: UUID?
    
    var name: String
    var skill: String
}

struct DesiredWorkoutsPerWeek: Codable {
    var start: Int8
    var end: Int8
}

struct ProfileData: Codable {
    let name: String
    let gender: String
    let interests: [Interest]
    let desired_workouts_per_week: DesiredWorkoutsPerWeek
    let favorite_exercises: [String]
    let age: Int
    let activity_level: String
}

