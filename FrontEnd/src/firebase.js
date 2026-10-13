import { initializeApp } from 'firebase/app'
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut as fbSignOut,
} from 'firebase/auth'

const firebaseConfig = {
  apiKey: 'AIzaSyDls91HFIf1_E0X6JJ1kuE7V8I6z8tW68A',
  authDomain: 'manajemen-risiko-98127.firebaseapp.com',
  projectId: 'manajemen-risiko-98127',
  storageBucket: 'manajemen-risiko-98127.firebasestorage.app',
  messagingSenderId: '465214376439',
  appId: '1:465214376439:web:73469cafb36d37c2b886f2',
  measurementId: 'G-FLYRRYCXEX',
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
const googleProvider = new GoogleAuthProvider()

export function signInWithGoogle() {
  return signInWithPopup(auth, googleProvider)
}

export function signOut() {
  return fbSignOut(auth)
}
