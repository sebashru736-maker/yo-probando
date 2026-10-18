import { Composition, Folder } from "remotion";
import { Avance3D, FinalConClips, OpeningScene, EndScene } from "./Video";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Avance3D"
        component={Avance3D}
        durationInFrames={360}
        fps={30}
        width={1080}
        height={1920}
      />
      <Folder name="Piezas-3D">
        <Composition
          id="Apertura3D"
          component={OpeningScene}
          durationInFrames={240}
          fps={30}
          width={1080}
          height={1920}
        />
        <Composition
          id="CierreTzubaru"
          component={EndScene}
          durationInFrames={120}
          fps={30}
          width={1080}
          height={1920}
        />
      </Folder>
      <Folder name="Montaje-con-clips">
        <Composition
          id="HBOFinal"
          component={FinalConClips}
          durationInFrames={960}
          fps={30}
          width={1080}
          height={1920}
        />
      </Folder>
    </>
  );
};
